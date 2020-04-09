# rps_calc

Simple rps calculator use python http server and prometheus metrics.

Command to start in docker:
`docker run --rm -p 8080:8080 -p 8081:8081 prostomak/rps_calc`


Params:

--NUMBER_REQUESTS - number requests that should count 

--TIME_FOR_CURRENT_RPS - seconds that use in current rps metrics  

--TIME_FOR_AVG_RPS - avg rps per this seconds


`docker run --rm -p 8080:8080 -p 8081:8081 prostomak/rps_calc --NUMBER_REQUESTS 100 --TIME_FOR_CURRENT_RPS 10 --TIME_FOR_AVG_RPS 60`
