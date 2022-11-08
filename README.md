# networkhw1
컴퓨터네트워크개론 UDP 시뮬레이터


# 무었입니까?
Server, Client 로 구성됩니다. Client는 Server에 요청을 보냅니다. Server는 요청을 받아 ack를 날립니다. 끝입니다.

# 무슨 기능을 구현합니까?

1. 서버는 요청에 대해 queue를 관리합니다. queue에 들어간 아이템은 일정 시간이 경과해야 큐를 탈출 할 수 있습니다.

2. 클라이언트는 congestion control을 합니다. drop rate가 커진다면 window의 크기를 줄일 필요가 있습니다. 또한, time out limit를 제어할 필요가 있습니다.
