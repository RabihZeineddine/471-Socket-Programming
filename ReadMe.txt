README.txt

Names and emails:
- Rabih Zein Eddine <rzeineddine@yahoo.com>,

Language: Python 3

Execution:
Server: python serv.py <port>
Client: python cli.py <server> <port>

Protocol overview:
- Control channel: newline-terminated text commands (`ls <port>`, `get <file> <port>`, `put <file> <port>`, `quit`).
- Data channel: raw bytes sent/received over a separate ephemeral TCP connection; end-of-stream (socket close) indicates completion.
- Robust send_all/recv_all loops ensure full transfers.

To Run use these commands on powershell

python serv.py 1234
python cli.py localhost 1234
