# Credential Cache

This subsystem allows for the management and caching of user
credentials for cloud infrastructures.  It generally follows the
resource schemas and CRUD operations for the [CIMI][cimi] standard.

The CIMI CRUD operations follow the usual REST patterns that use the
HTTP POST, GET, PUT, and DELETE actions.  The only slight difference
is that for some resources (credentials in particular) the create
operation takes a CredentialTemplate resource rather than a Credential
resource.

## User Workflow

This was developed primarily to allow users to delegate a time-limited
proxy to the SlipStream server via the MyProxy/VOMS servers used
within EGI.  The workflow for users is the following:

  * Users must create a short-lived credential on the MyProxy server
    protected with a temporary username and password.  This can be
    done with the command:
    
        myproxy-init -l random_username -c 1

  * User must also create a long-lived credential on the MyProxy
    server that allows renewals by holders of a valid proxy.  This can
    be done with the command:
    
        myproxy-init -d -x -R 'full DN, globus fmt'

  * The user then edits their SlipStream user parameters, providing
    the temporary username/password of the short-lived credential.
    The user may also provide an email address for renewal failure
    notifications and a lifetime (in seconds) for renewed credentials.
    Note that SlipStream will automatically retrieve and then delete
    the short-lived credential on the MyProxy server.

  * The user must maintain an active long-lived credential on the
    MyProxy server to allow credential renewals.  The server will
    attempt renewals until the credential validity falls below 6
    minutes.  Users are notified of failure if they provide an email
    address and the SlipStream server is configured with SMTP 
    parameters.

  * If the credential on the server expires, the user must delegate a
    new credential to the server via this procedure.

If the user provides VOMS information, then the credential cache will
also create proxies that contain VOMS attribute certificates.

## SlipStream Integration

The main entry point for the system from clojure is the namespace:

    slipstream.credcache.control

where the functions `start!` and `stop!` must be called when
SlipStream is started and stopped, respectively.

The `start!` function takes no arguments.  

The `stop!` function also takes no arguments.  It is **extremely**
important that the `stop!` function be called on termination.  If it is
not called, threads for the job scheduling will not be stopped
preventing the JVM from exiting.

A wrapper class has been created that makes it easier to use the
core features of the system from Java.  This class is
`slipstream.credcache.javawrapper` and contains four static methods:

  * `void start()`: must be called at the SlipStream server start
  * `void stop()`: must be called before stopping the SlipStream server
  * `String create(Map template)`: does the initial delegation of a
    proxy to the server.  See the MyProxyVomsCredentialTemplate value
    for the schema of the template.
  * `File retrieve(String id)`: Retrieve the given proxy and writes it
    to a temporary file.  The caller is responsible for deleting the
    temporary file.

Integration of the MyProxy/VOMS functionality will also require that
the EGI certificates and VOMS servers are configured correctly on the
SlipStream server.

## Manual Testing from REPL

### Start the REPL

To start a clojure REPL from the command line, change your directory
to the java/jar submodule.  Then invoke the command:

    mvn clean clojure:repl
    
This will start a REPL with all of the necessary software on the 
classpath.

From the REPL itself, follow the steps below.  

### Start the Quartz Scheduler

First require the control namespace and start the Quartz job 
scheduler.

    (require '[slipstream.credcache.control :as ctl])
    (ctl/start!)
    
This should produce some logging information that indicates at the 
end that the Quartz scheduler has been started.

### Delegate Credentials to MyProxy Server

Next, the appropriate credentials must be delegated to the MyProxy
server: a long-lived proxy (delegation proxy) and a short-lived
proxy (bootstrap proxy).

This can be done via the command line following the instructions
in the "user workflow" section above.  This comes down to running
`myproxy-init` twice.

Or you can do the equivalent from the REPL itself (**warning
this code is currently not working!**):

    (require '[slipstream.credcache.workflows :refer :all])
    
    (def passphrase "changeme")
    (def delegation-params (upload-delegation-proxy passphrase))
    (def bootstrap-params (upload-bootstrap-proxy passphrase))
    
Change the passphrase to correspond to the one used for your grid
certificate.  This will use the default MyProxy server configured in
the code ("myproxy.hellasgrid.gr").  Add parameters to the above 
commands to change this, if necessary.

### Update Credential Cache Location

If necessary, change the location of the credential cache on the 
local disk:

    (require '[slipstream.credcache.db-utils :as db])
    (alter-var-root #'db/*cache-dir* (constantly "/home/loomis/credcache"))
    
The default location `/opt/slipstream/server/credcache/` may not
exist or be accessible as a normal user.  **The directory that you 
choose must exist.**

### Create Credential in Cache

Now create a new MyProxy credential within the server.  This will
register a new proxy and initiate the jobs to maintain a valid 
credential on the server.

    (require '[slipstream.credcache.credential :as crud])
    
    ;; If you've delegated your credentials via the command line
    ;; with myproxy-init, define the bootstrap parameters as follows
    ;; 
    ;; If you've done this in the REPL, this is already defined.
    (def bootstrap-params
      {:myproxy-host "myproxy.hellasgrid.gr"
       :myproxy-port 7512
       :username "random_username"
       :passphrase "changeme"})
       
    ;; If you want to create a proxy with VOMS extensions,
    ;; then do the following, changing the VO name as appropriate:
    (def bootstrap-params
      (-> bootstrap-params
          (assoc :voms {"fedcloud.egi.eu" {}})))

    ;; Create the template for generating the credential.        
    (def template
      (-> bootstrap-params
          (select-keys [:myproxy-host :myproxy-port :username :passphrase :voms])
          (assoc :typeURI "http://schemas.dmtf.org/cimi/1/CredentialTemplate")
          (assoc :subtypeURI "http://sixsq.com/slipstream/credential/myproxy-voms")
          (assoc :email "user@example.com")
          (assoc :lifetime (* 15 60))))

    ;; Finally, actually create it.
    (def credential-uuid (crud/create template))
    
This should print logging information indicating that a credential 
has been created and that a renewal job has been scheduled.  This 
renewal should be scheduled for 2/3 of the validity period of the 
credential.

You can check that the credential has been created in the credential
cache directory.  It should have the name of the returned identifier.

### Check Proxy Contents

Retrieve the proxy from the credential cache via the REPL:

    (def cred (crud/retrieve credential-uuid))

Now write this proxy to a separate file.
    
    (require '[slipstream.credcache.voms-utils :as voms])
    (-> cred
        (:proxy)
        (voms/base64->proxy)
        (voms/proxy->file "vproxy-retrieved.pem"))

This can then be checked at the command line by running the command
`voms-proxy-info`:

    $ voms-proxy-info -all -file vproxy-retrieved.pem
    
This should print out the information about the certificate itself
and any contained attribute certificates.

### Proxy Renewal

When the renewal job runs, you should see logging information that
indicates that the proxy has been renewed and that a new renewal job
has been scheduled.

To remove the long-lived delegation credential to force the renewal
to fail, do the following:

    (require '[slipstream.credcache.myproxy-utils :as myproxy])
    (myproxy/destroy-proxy delegation-params)

or use the command line:

    $ myproxy-destroy -d

You must have a valid local proxy for this command to work.

The logging for the next scheduled removal should notify you that
the renewal has failed.  It should also schedule another renewal job
if the remaining time isn't too close.  If the record contains an
email address and the SlipStream configuration contains SMTP
parameters, then it should also send an email about the failure.

### Stop the Quartz Scheduler

To stop the job scheduler, do the following:

    (ctl/stop!)

You can restart the procedure from the beginning at this point.


[cimi]: http://dmtf.org/sites/default/files/standards/documents/DSP0263_1.1.0.pdf
