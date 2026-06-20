// Minimal mbedTLS message-digest mock (host syntax check only).
#pragma once
#include <cstddef>

typedef enum { MBEDTLS_MD_SHA256 } mbedtls_md_type_t;
struct mbedtls_md_info_t;

const mbedtls_md_info_t* mbedtls_md_info_from_type(mbedtls_md_type_t type);
int mbedtls_md_hmac(const mbedtls_md_info_t* info,
                    const unsigned char* key, size_t keylen,
                    const unsigned char* input, size_t ilen,
                    unsigned char* output);
