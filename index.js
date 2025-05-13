url = "http://localhost:11434/api/chat"
async function main() {

	let out_obj = {
		"model": "llama3.2:1b",
		"messages": [
			{
				"role": "user",
				"content": "a story about a tall lanky red haired boy that throws out sentient trash named martin"
			}
		],
		"stream": false
	}

	let out_str = await JSON.stringify(out_obj)
	let resp = await fetch(url, {
		method: "POST",
		body: out_str,
	})

	let obj = await resp.json()
	console.log(obj["message"]["content"])

}
main()
