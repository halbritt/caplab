from hookline.signing import sign_payload, verify_signature


def test_signature_round_trip():
    body = b'{"id":"abc","kind":"invoice.paid"}'
    signature = sign_payload(b"s3cret", body)
    assert verify_signature(b"s3cret", body, signature)


def test_signature_rejects_tampered_body():
    signature = sign_payload(b"s3cret", b"original")
    assert not verify_signature(b"s3cret", b"tampered", signature)


def test_signature_depends_on_secret():
    body = b"payload"
    assert sign_payload(b"secret-a", body) != sign_payload(b"secret-b", body)
