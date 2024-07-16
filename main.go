package main

import (
	"net/http"

	"github.com/gorilla/mux"
)

func HealthCheck(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Golang rules bitches!"))
}

func main() {
	router := mux.NewRouter()
	// setting up endpoints
	router.HandleFunc("/healthcheck", HealthCheck).Methods("GET")
	// starting listener
	http.ListenAndServe(":6969", router)
}
