for (const element of document.getElementsByClassName("cards")) {
    element.onmousemove = e => {
        for (const card of document.getElementsByClassName("card")) {

            const rect = card.getBoundingClientRect(),
                x = e.clientX - rect.left,
                y = e.clientY - rect.top;

            card.style.setProperty("--mouse-x", `${x}px`);
            card.style.setProperty("--mouse-y", `${y}px`);
        }
    }
}

///////////////////////////////////////
const phoneNumber = "+421918215490";
const phoneLink = document.getElementById("phone-link");

console.log(phoneLink);

function isMobileDevice() {
    return /Mobi|Android|iPhone/i.test(navigator.userAgent);
}

console.log(isMobileDevice());

if (isMobileDevice()) {
    phoneLink.href = `tel:${phoneNumber}`;
} else {
    console.log("here")
    phoneLink.href = "#";
    phoneLink.addEventListener("click", function (event) {
        event.preventDefault();
        navigator.clipboard.writeText(phoneNumber)
            .then(() => alert("Phone number copied to clipboard!"))
            .catch(err => console.error("Error copying phone number:", err));
    });
}

/////////////////////////////////////////
const slider = document.getElementById("slider");
const text = document.getElementById("box-count");
count = 1;

document.getElementById("next").addEventListener("click", () => {
    if (count < 5) {
        count += 1;
        text.innerHTML = count + " / 5";
    }
    slider.scrollTo({ left: (count - 1) * (window.innerWidth - 10), behavior: 'smooth' });
});

document.getElementById("prev").addEventListener("click", () => {
    if (count > 1) {
        count -= 1;
        text.innerHTML = count + " / 5";
    }
    slider.scrollTo({ left: (count - 1) * (window.innerWidth - 10), behavior: 'smooth' });
});

window.addEventListener("resize", () => {
    slider.scrollTo({ left: 0, behavior: 'smooth' });
    count = 1;
    text.innerHTML = count + " / 5";
});

///////////////////////////////////////////
const points = document.querySelectorAll('.point');
const images = document.querySelectorAll('.img img');
const titles = document.querySelectorAll('.point .title')
const texts = document.querySelectorAll('.point .text')

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const index = entry.target.dataset.index;
            images.forEach(img => img.classList.remove('active'));
            titles.forEach(img => img.classList.remove('active'));
            texts.forEach(img => img.classList.remove('active'));
            const matchingImage = document.querySelector(`.img img[data-index="${index}"]`);
            const title = document.querySelector(`.point .title[data-index="${index}"]`)
            const text = document.querySelector(`.point .text[data-index="${index}"]`)
            if (matchingImage) {
                matchingImage.classList.add('active');
            }
            if (title) {
                title.classList.add("active");
            }
            if (text) {
                text.classList.add("active");
            }
        }
    });
}, {
    root: null,
    threshold: 1
});

points.forEach(point => observer.observe(point));

//////////////////////////////////////////////////
const userLang = navigator.language || navigator.userLanguage;
console.log("User language is:", userLang);