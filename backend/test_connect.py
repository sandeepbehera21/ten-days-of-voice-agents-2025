import socket
import ssl
import sys

hostname = "api.deepgram.com"
port = 443

print(f"Testing connectivity to {hostname}:{port}...")

try:
    # Test DNS resolution
    print("Resolving DNS...")
    addr_info = socket.getaddrinfo(hostname, port)
    print(f"DNS Resolved: {addr_info}")
except Exception as e:
    print(f"DNS Resolution Failed: {e}")
    sys.exit(1)

try:
    # Test TCP connection
    print("Connecting TCP...")
    sock = socket.create_connection((hostname, port), timeout=5)
    print("TCP Connected.")
    
    # Test SSL handshake
    print("Performing SSL Handshake...")
    context = ssl.create_default_context()
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(f"SSL Handshake Successful. Cipher: {ssock.cipher()}")
        ssock.close()
    
    print("Connectivity Test Passed.")
except Exception as e:
    print(f"Connection Failed: {e}")
    sys.exit(1)
