let model1 = document.querySelector("#popup1");
let model2 = document.querySelector("#popup2");
let model3 = document.querySelector("#popup3");
let model4 = document.querySelector("#popup4");
let model5 = document.querySelector("#popup5");
let cancel = document.querySelectorAll(".but1_1");
let next = document.querySelectorAll(".but2_1");
let submit = document.querySelector(".but2_1_sub");
let eligibility = document.querySelector("#but_eli");

let models = [model1, model2, model3, model4, model5];
let count = 0;

if (eligibility) {
    eligibility.onclick = (event) => {
        event.preventDefault();
        count = 0;
        models.forEach(m => { if (m) m.style.display = "none"; });
        if (model1) {
            model1.style.display = "flex";
            model1.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    };
}

function validateCurrentStep(stepIndex) {
    if (!models[stepIndex]) return true;
    let inputs = models[stepIndex].querySelectorAll("input, select, textarea");
    for (let input of inputs) {
        if (!input.checkValidity()) {
            input.reportValidity();
            return false;
        }
    }
    return true;
}

cancel.forEach((button) => {
    button.onclick = (event) => {
        event.preventDefault();

        if (count === 0) {
            if (model1) model1.style.display = "none";
        } else if (count > 0 && count < models.length) {
            if (models[count]) models[count].style.display = "none";
            count--;
            if (models[count]) {
                models[count].style.display = "flex";
                models[count].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    };
});

next.forEach((button) => {
    button.onclick = (event) => {
        event.preventDefault();

        if (!validateCurrentStep(count)) {
            return;
        }

        if (count < models.length - 1) {
            if (models[count]) models[count].style.display = "none";
            count++;
            if (models[count]) {
                models[count].style.display = "flex";
                models[count].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    };
});