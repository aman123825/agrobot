// Minimal TinyGPS++ mock (host syntax check only).
#pragma once

class TinyGPSLocation {
public:
    bool          isValid() { return false; }
    double        lat() { return 0.0; }
    double        lng() { return 0.0; }
    unsigned long age() { return 0; }
};

class TinyGPSPlus {
public:
    TinyGPSLocation location;
    bool encode(char c) { (void)c; return false; }
};
