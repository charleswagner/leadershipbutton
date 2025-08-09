"https://texttospeech.googleapis.com/v1/text:synthesize" > response.json
% Total % Received % Xferd Average Speed Time Time Time Current
Dload Upload Total Spent Left Speed
100 49772 0 49433 100 339 99k 697 --:--:-- --:--:-- --:--:-- 100k
cwagner@Charless-MacBook-Pro leadershipbutton % curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json; charset=utf-8" \
-H "X-Goog-User-Project: leadershipbutton" \
-d @request2.json \
"https://texttospeech.googleapis.com/v1/text:synthesize" > response.json
% Total % Received % Xferd Average Speed Time Time Time Current
Dload Upload Total Spent Left Speed
100 49772 0 49433 100 339 66399 455 --:--:-- --:--:-- --:--:-- 66808
cwagner@Charless-MacBook-Pro leadershipbutton % cat response.json | grep "audioContent" | awk -F'"' '{print $4}' | base64 --decode > gcloud-output.mp3
cwagner@Charless-MacBook-Pro leadershipbutton % open gcloud-output.mp3
cwagner@Charless-MacBook-Pro leadershipbutton %
