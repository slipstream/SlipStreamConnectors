;
; Copyright (c) 2014.
; SixSq Sarl (http://sixsq.com) and EGI.eu (http://egi.eu).
;
; Licensed under the Apache License, Version 2.0 (the "License")
; you may not use this file except in compliance with the License.
; You may obtain a copy of the License at
;
;     http://www.apache.org/licenses/LICENSE-2.0
;
; Unless required by applicable law or agreed to in writing, software
; distributed under the License is distributed on an "AS IS" BASIS,
; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
; See the License for the specific language governing permissions and
; limitations under the License.
;

(ns slipstream.credcache.notify-test
  (:require
    [expectations :refer :all]
    [slipstream.credcache.notify :refer :all]))

(expect 10 (str->int 10))
(expect 10 (str->int "10"))
(expect "bad" (str->int "bad"))
(expect "0xff" (str->int "0xff"))

(expect {:alpha "OK"} (convert-port {:alpha "OK"}))
(expect {:port 10} (convert-port {:port 10}))
(expect {:port 10} (convert-port {:port "10"}))
(expect {:port "bad"} (convert-port {:port "bad"}))
