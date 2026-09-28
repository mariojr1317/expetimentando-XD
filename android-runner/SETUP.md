# Android Runner setup

This is the actual Android environment we will use for Universal App Runner.

## 1. Host

Use a Linux machine with Docker, Docker Compose and KVM. Google documents KVM as a requirement for the container images. Cloud VMs can work when they expose nested virtualization, although Google warns that nested virtualization reduces performance.

## 2. Start the Android emulator

From this directory:

```bash
docker compose up -d emulator
```

Then verify ADB from the host:

```bash
adb connect 127.0.0.1:5555
adb devices
```

The emulator's native gRPC/WebRTC service is on port 8554.

## 3. Browser streaming

Google's container project includes a Python gateway and a React WebRTC client. The gateway translates browser REST/WebSocket signaling into the emulator's native gRPC RTC service. The WebRTC channel carries the video/audio and the input data channel carries mouse, touch, keyboard and wheel events.

That is the path we will use instead of screenshot polling, because screenshot polling adds unnecessary latency.

Official project:
https://github.com/google/android-emulator-container-scripts

Official browser client:
https://github.com/google/android-emulator-webrtc

## 4. APK installation

The Universal App Runner backend already knows how to send an uploaded APK to an external Android Runner through:

```
POST /sessions
Authorization: Bearer <ANDROID_RUNNER_TOKEN>
multipart/form-data:
  session_id
  file
```

The remaining connection is the runner-side ADB installation endpoint and the authenticated WebRTC gateway URL.

## Important security

Do not expose port 5555/ADB directly to the public internet. Keep ADB on the private runner network. Only the authenticated WebRTC gateway should be reachable by the browser.

## Performance

Use KVM. If the host has GPU acceleration available, Google's scripts also support GPU-backed emulator containers. For a remote deployment, the network path matters too: the browser and runner should be geographically/network-close where practical.
