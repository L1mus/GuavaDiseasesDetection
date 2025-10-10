const homePage = document.getElementById("homePage");
const resultPage = document.getElementById("resultPage");
const fileInput = document.getElementById("fileInput");
const backButton = document.getElementById("backButton");
const uploadedImage = document.getElementById("uploadedImage");

const exampleResult = {
  prediction: "Karat Merah",
  confidence: "95.40%",
  imageSrc: "https://i.ibb.co/3cqB4Jc/daun-karat.jpg",
  info: "Karat merah atau Red Rust disebabkan oleh ganggang Cephaleuros virescens. Menyerang daun, batang, dan buah, menyebabkan bercak oranye kemerahan seperti beludru.",
  suggestion:
    "Lakukan sanitasi kebun, pangkas bagian yang terinfeksi berat. Semprotkan fungisida berbasis tembaga untuk mengendalikan penyebaran ganggang.",
};

function showPage(pageToShow) {
  const pages = [homePage, resultPage];
  pages.forEach((page) => {
    if (page === pageToShow) {
      page.classList.remove("page-hidden");
      page.style.position = "relative";
    } else {
      page.classList.add("page-hidden");
      page.style.position = "absolute";
    }
  });
}

fileInput.addEventListener("change", function (event) {
  if (event.target.files && event.target.files[0]) {
    const reader = new FileReader();

    reader.onload = function (e) {
      uploadedImage.src = e.target.result;
      document.getElementById("predictionResult").textContent =
        exampleResult.prediction;
      document.getElementById(
        "confidenceScore"
      ).textContent = `Keyakinan ${exampleResult.confidence}`;
      document.getElementById("diseaseInfo").textContent = exampleResult.info;
      document.getElementById("handlingSuggestion").textContent =
        exampleResult.suggestion;

      showPage(resultPage);
    };

    reader.readAsDataURL(event.target.files[0]);
  }
});
backButton.addEventListener("click", function () {
  fileInput.value = "";
  showPage(homePage);
});
document.addEventListener("DOMContentLoaded", () => {
  showPage(homePage);
});
