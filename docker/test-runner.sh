#!/bin/sh
set -e

echo "Starting minimal Python RPyC server on port 18812..."
python /app/fake_mt5_server.py > /tmp/server.log 2>&1 &
SERVER_PID=$!
echo "RPyC server started (PID: $SERVER_PID)"

sleep 2

echo "Checking server reachability..."
python -c "
import socket
s = socket.socket()
s.settimeout(2)
r = s.connect_ex(('localhost', 18812))
s.close()
print('Server reachable' if r == 0 else 'Not reachable: code ' + str(r))
"

echo "Testing rpyc connection directly..."
timeout 10 python -c "
import rpyc
print('Attempting rpyc.classic.connect...')
conn = rpyc.classic.connect('localhost', 18812)
print('Connected!')
conn.close()
print('Connection test passed')
" 2>&1 || echo "Connection test failed or timed out"

echo "Running standalone engine tests..."
timeout 60 python -m pytest tests/e2e/test_standalone_engine.py -v --tb=short 2>&1 || echo "Tests timed out or failed"
RESULT=$?

echo "=== server log ==="
cat /tmp/server.log
echo "=================="

echo "Cleaning up..."
kill $SERVER_PID 2>/dev/null || true

exit $RESULT
