package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

type RespData struct {
	Time    string `json:"time,omitempty"`
	Version string `json:"version,omitempty"`
}

var (
	httpSuccess = promauto.NewCounter(prometheus.CounterOpts{
		Name: "canary_http_success_total",
		Help: "Number of 200 responses",
	})

	httpError = promauto.NewCounter(prometheus.CounterOpts{
		Name: "canary_http_errors_total",
		Help: "Number of 500 responses",
	})

	respDuration = promauto.NewHistogram(prometheus.HistogramOpts{
		Name:    "canary_response_duration",
		Help:    "Duration in seconds to process response to requests",
		Buckets: []float64{1000, 10000},
	})
)

func GetTimeData(w http.ResponseWriter, r *http.Request) {
	startTime := time.Now()
	log.Println("Time data requested")

	var respData []RespData
	nowTimestamp := time.Now().UTC().String()
	respData = append(respData, RespData{Time: nowTimestamp})

	json.NewEncoder(w).Encode(respData)

	httpSuccess.Inc()
	log.Println("Time data delivered")
	duration := time.Now().Sub(startTime)
	respDuration.Observe(float64(duration / time.Millisecond))
}

func GetVersionData(w http.ResponseWriter, r *http.Request) {
	startTime := time.Now()
	log.Println("Version data requested")

	var respData []RespData
	content, err := ioutil.ReadFile("/VERSION")
	if err != nil {
		log.Println("Failed to read version file: ", err)
	}
	version := string(content)
	respData = append(respData, RespData{Version: version})

	json.NewEncoder(w).Encode(respData)

	httpSuccess.Inc()
	log.Println("Version data delivered")
	duration := time.Now().Sub(startTime)
	respDuration.Observe(float64(duration / time.Millisecond))
}

func GetVersionDataError(w http.ResponseWriter, r *http.Request) {
	startTime := time.Now()
	log.Println("Version data requested")

	dieRoll := rand.Int()
	if dieRoll%2 == 0 {
		w.WriteHeader(http.StatusInternalServerError)
		fmt.Fprintf(w, "Internal Server Error\n")
		httpError.Inc()
		log.Println("Internal server error returned")
	} else {
		var respData []RespData
		content, err := ioutil.ReadFile("/VERSION")
		if err != nil {
			log.Println("Failed to read version file: ", err)
		}
		version := string(content)
		respData = append(respData, RespData{Version: version})

		json.NewEncoder(w).Encode(respData)

		httpSuccess.Inc()
		log.Println("Version data delivered")
	}
	duration := time.Now().Sub(startTime)
	respDuration.Observe(float64(duration / time.Millisecond))
}

func GetVersionDataSlow(w http.ResponseWriter, r *http.Request) {
	startTime := time.Now()
	log.Println("Version data requested")

	dieRoll := rand.Int()
	if dieRoll%2 == 0 {
		time.Sleep(5 * time.Second)
	}

	var respData []RespData
	content, err := ioutil.ReadFile("/VERSION")
	if err != nil {
		log.Println("Failed to read version file: ", err)
	}
	version := string(content)
	respData = append(respData, RespData{Version: version})

	json.NewEncoder(w).Encode(respData)

	httpSuccess.Inc()
	log.Println("Version data delivered")
	duration := time.Now().Sub(startTime)
	respDuration.Observe(float64(duration / time.Millisecond))
}

func main() {
	log.Println("Starting meshlab data service")

	args := os.Args
	arg := ""
	if len(args) > 1 {
		arg = args[1]
	}

	if arg == "error" {
		http.HandleFunc("/version", GetVersionDataError)
	} else if arg == "slow" {
		http.HandleFunc("/version", GetVersionDataSlow)
	} else {
		http.HandleFunc("/version", GetVersionData)
	}

	http.Handle("/metrics", prometheus.Handler())

	http.HandleFunc("/timedata", GetTimeData)

	http.ListenAndServe(":8080", nil)
}
