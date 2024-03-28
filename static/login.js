function toggleSignUp() {
    var loginForm = document.querySelector(".login-form");
    var signUpForm = document.querySelector(".signup-form");
  
    if (loginForm.style.display !== "none") {
      loginForm.style.display = "none";
      signUpForm.style.display = "block";
    } else {
      signUpForm.style.display = "none";
      loginForm.style.display = "block";
    }
  }
  