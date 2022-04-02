echo 'statcert www.google.com'
statcert www.google.com
echo 'statcert www.google.com www.twitter.com'
statcert www.google.com www.twitter.com
echo 'statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3-5'
statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3-5
echo 'statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 10'
statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 10
echo 'statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3 -o "stat-test.csv"'
statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3 -o "stat-test.csv"
echo 'statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3 -o "stat-test.json"'
statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3 -o "stat-test.json"
echo 'statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3 -o "stat-test.txt"'
statcert /home/kalil/code/statcert/top-1m-2022-02-01.csv -n 3 -o "stat-test.txt"
echo 'statcert -n 3'
statcert -n 3
echo 'statcert -n 3 --rand'
statcert -n 3 --rand
