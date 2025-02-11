const getMe = async () => {
    const accessToken = localStorage.getItem("access_token");
    console.log(accessToken)

    if (!accessToken) {
        alert("دسترسی غیرمجاز! لطفا وارد شوید.");
        location.href = "admin/login";
        return;
    }

    try {
        console.log(3)
        const response = await fetch("http://127.0.0.1:8000/api/admin/get_me", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${accessToken}`,
                "Content-Type": "application/json",
            },
        });

        if (response.status === 200) {
            alert("dasdad")
            const result = await response.json();
            console.log("User Data:", result);

            // Display username in the navbar if needed
            const profileLink = document.querySelector("#profile-link");
            if (profileLink) {
                profileLink.textContent = `👤 ${result.username}`;
            }
        } else {
            alert("شما اجازه دسترسی به این صفحه را ندارید.");
            location.href = "login";
        }
    } catch (error) {
        console.error("خطا در دریافت اطلاعات کاربر:", error);
        alert("خطایی رخ داده است. لطفا دوباره تلاش کنید.");
        location.href = "admin/login";
    }
};

// Ensure authentication before the page loads
document.addEventListener("DOMContentLoaded", getMe);