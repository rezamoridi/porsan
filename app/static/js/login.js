const login = async () => {
    const usernameInputElem = document.querySelector(".username");
    const passwordInputElem = document.querySelector(".password");
    const data = new URLSearchParams();
    data.append("username", usernameInputElem.value.trim());
    data.append("password", passwordInputElem.value.trim());
    data.append("grant_type", "password");

    try {
        const response = await fetch(`http://127.0.0.1:8000/api/auth/admin/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: data.toString(),
        });

        const result = await response.json();
        document.cookie = `access_token=${result.access_token}; path=/; secure`;
        
        if (response.status === 200) {
            alert("با موفقیت وارد شدید!");
            
            

            // Store the token as a cookie


            // Redirect to the admin page
            location.href = "/admin/dashboard";
        } else if (response.status === 401) {
            alert("اطلاعات واردشده اشتباه میباشد");
        } else if (response.status === 422) {
            alert("متاسفانه خطایی رخ داده است لطفا مجددا تلاش فرمایید.");
        } else if (response.status === 400) {
            alert("کاربر مورد نظر یافت نشد.");
        } else {
            alert("خطایی رخ داده است. لطفا دوباره تلاش کنید.");
        }

        // Clear inputs regardless of the response status
        clearInputs(usernameInputElem, passwordInputElem);

    } catch (error) {
        console.error("An error occurred during login:", error);
        alert("خطایی رخ داده است. لطفا دوباره تلاش کنید.");
    }
};

// Function to clear input fields
const clearInputs = (usernameElem, passwordElem) => {
    usernameElem.value = "";
    passwordElem.value = "";
};

// Attach event listener to the form
window.addEventListener("load", () => {
    const loginForm = document.querySelector("#loginForm");
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault(); // Prevent form submission
        login(); // Call the login function
    });
});