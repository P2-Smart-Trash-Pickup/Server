package main

import (
	"encoding/json"
	"fmt"
	"github.com/gin-gonic/gin"
	"io"
	"os"
	"slices"
)

func load_plan(path string, out_plan *[][][]float32) {

	jsonFile, err := os.Open(path)
	if err != nil {
		fmt.Println(err)
	}
	byteValue, _ := io.ReadAll(jsonFile)

	var plan [][][]float32
	json.Unmarshal([]byte(byteValue), &plan)

	*out_plan = plan

	jsonFile.Close()
}

func main() {

	router := gin.Default()

	router.GET("/moloks", func(c *gin.Context) {

		c.Header("Access-Control-Allow-Origin", "*")

		jsonFile2, err := os.Open("../../../data/molokker.json")
		if err != nil {
			fmt.Println(err)
		}
		byteValue2, _ := io.ReadAll(jsonFile2)

		var moloks []map[string]any
		json.Unmarshal([]byte(byteValue2), &moloks)

		jsonFile2.Close()
		c.JSON(200, gin.H{
			"msg": moloks,
		})
	})

	router.GET("/cust_plan", func(c *gin.Context) {

		c.Header("Access-Control-Allow-Origin", "*")

		var cust_plan [][][]float32
		load_plan("../../../data/cust_plan.json", &cust_plan)
		c.JSON(200, gin.H{
			"msg": cust_plan,
		})
	})

	router.GET("/default_nord_plan", func(c *gin.Context) {

		c.Header("Access-Control-Allow-Origin", "*")

		var default_nord_plan [][][]float32
		load_plan("../../../data/default_nord_plan.json", &default_nord_plan)
		c.JSON(200, gin.H{
			"msg": default_nord_plan,
		})
	})

	router.GET("/optimized_nord_plan", func(c *gin.Context) {

		c.Header("Access-Control-Allow-Origin", "*")
		var optimized_nord_plan [][][]float32
		load_plan("../../../data/optimized_nord_plan.json", &optimized_nord_plan)
		c.JSON(200, gin.H{
			"msg": optimized_nord_plan,
		})
	})

	router.GET("/optimized_nord_energy", func(c *gin.Context) {

		c.Header("Access-Control-Allow-Origin", "*")

		var optimized_nord_energy [][][]float32
		load_plan("../../../data/optimized_nord_energy.json", &optimized_nord_energy)
		c.JSON(200, gin.H{
			"msg": optimized_nord_energy,
		})
	})

	router.GET("/optimized_cust_energy", func(c *gin.Context) {

		c.Header("Access-Control-Allow-Origin", "*")

		var optimized_nord_energy [][][]float32
		load_plan("../../../data/optimized_day_14.json", &optimized_nord_energy)
		c.JSON(200, gin.H{
			"msg": optimized_nord_energy,
		})
	})

	router.GET("/:route", func(c *gin.Context) {

		var cache [709][][][]float32

		jsonFile, err := os.Open("../../../data/molok_polyline_matrix2.json")
		if err != nil {
			fmt.Println(err)
		}

		defer jsonFile.Close()

		decoder := json.NewDecoder(jsonFile)
		decoder.Token()
		var route []int

		route_str := c.Param("route")
		json.Unmarshal([]byte(route_str), &route)

		var data [][][]float32
		iterations := 0
		for decoder.More() {
			if iterations == slices.Max(route)+1 {
				break
			}
			decoder.Decode(&data)
			if slices.Contains(route, iterations) {
				cache[iterations] = data
			}
			iterations += 1
		}

		var poly_route [][][]float32
		for i := 0; i < len(route)-1; i++ {
			curr_point := route[i]
			next_point := route[i+1]
			temp_val := cache[curr_point][next_point]
			poly_route = append(poly_route, temp_val)
		}

		out := poly_route

		c.Header("Access-Control-Allow-Origin", "*")
		c.JSON(200, gin.H{
			"msg": out,
		})
	})
	router.Run() // listen and serve on 0.0.0.0:8080
}
