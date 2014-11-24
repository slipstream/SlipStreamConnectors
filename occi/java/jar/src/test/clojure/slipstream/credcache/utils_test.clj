(ns slipstream.credcache.utils-test
  (:require
    [expectations :refer :all]
    [slipstream.credcache.utils :refer :all])
  (:import
    [java.io File]))

;; random-char
(expect Character (random-char))

;; random-string
(expect "" (random-string 0))
(expect "" (random-string -1))
(expect String (random-string 1))
(expect #"^[\da-z]{27}$" (random-string 27))

;; file->byte-array, byte-array->file with File
(let [tfile (File/createTempFile "credcache" ".bin")
      bytes (byte-array (map byte (repeatedly 1024 random-char)))]
  (expect nil (byte-array->file bytes tfile))
  (expect (seq bytes) (seq (file->byte-array tfile))))

;; base64 utilities
(let [raw-bytes (.getBytes (random-string 2048))
      base64 (bytes->base64 raw-bytes)
      bytes (base64->bytes base64)]
  (expect (seq raw-bytes) (seq bytes)))

;; random UUID
(expect String (random-uuid))
(expect #"\p{XDigit}{8}-(?:\p{XDigit}{4}-){3}\p{XDigit}{12}" (random-uuid))

;; file->byte-array, byte-array->file with String path
;; FIXME: Determine why doing this back-to-back with above test fails!
(let [tfile (.getPath (File/createTempFile "credcache" ".bin"))
      bytes (byte-array (map byte (repeatedly 1024 random-char)))]
  (expect nil (byte-array->file bytes tfile))
  (expect (seq bytes) (seq (file->byte-array tfile))))


