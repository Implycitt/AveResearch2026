package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
)

func grabData(url string) nil {
	response, err := http.get(url)

	if err != nil {
		fmt.print(err.Error())
		os.Exit(1)
	}

	responseData, err := io.ReadAll(response.Body)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(string(responseData))
}
