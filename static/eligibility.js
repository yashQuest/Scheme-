let model1 = document.querySelector("#popup1");
let model2 = document.querySelector("#popup2");
let model3 = document.querySelector("#popup3");
let model4 = document.querySelector("#popup4");
let model5 = document.querySelector("#popup5");
let cancel = document.querySelectorAll(".but1_1");
let next = document.querySelectorAll(".but2_1");
let submit = document.querySelector(".but2_1_sub");
let eligibility = document.querySelector("#but_eli")



let count = 0;


eligibility.onclick = (event) => {
    event.preventDefault();
    model1.style.display = "flex";
}



cancel.forEach((button) => {


    button.onclick = (event) => {

        event.preventDefault();

        if (count === 0) {
            model1.style.display = "none";
            
        }

        else if (count === 1) {
            model2.style.display = "none";
            model1.style.display = "flex";
        }

        else if (count === 2) {
            model3.style.display = "none";
            model2.style.display = "flex";
        }

        else if (count === 3) {
            model4.style.display = "none";
            model3.style.display = "flex";
        }
        else if (count === 4) {
            model5.style.display = "none";
            model4.style.display = "flex";
        }

        count--;
    };

});

next.forEach((button) => {


    button.onclick = (event) => {

        event.preventDefault();

        if (count === 0) {
            model1.style.display = "none";
            model2.style.display = "flex";
        }

        else if (count === 1) {
            model2.style.display = "none";
            model3.style.display = "flex";
        }

        else if (count === 2) {
            model3.style.display = "none";
            model4.style.display = "flex";
        }

        else if (count === 3) {
            model4.style.display = "none";
            model5.style.display = "flex";
        }

        count++;
    };

});