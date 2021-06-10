	async function addSubscriber(){
		let form = document.getElementById("subscribe-form")

		let email = document.getElementById("email").value

		config = {
			method: "POST",
			body: JSON.stringify({email}),
			headers: {
				'X-CSRFToken': document.getElementsByName("csrfmiddlewaretoken")[0].value,
				'Content-Type': 'application/json',
			}
		}
		
		let subscription = document.getElementById("subscription")
		document.getElementById("subscribe-spinner").classList.remove("d-none")
		await fetch('/subscribe', config)
			.then(res => {
				console.log(res)
				if(res.status==409) subscription.innerHTML = "This email already exists."
				else if(res.status==200) subscription.innerHTML = "Your email is successfully added."
				else subscription.innerHTML = "Some error occured."
			})
			.catch(e => {
				console.log(e)})
		document.getElementById("subscribe-spinner").classList.add("d-none")
		form.reset()
	}
