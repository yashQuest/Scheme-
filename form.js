let open = document.querySelector("#openBtn");
let close = document.querySelector("#closeBtn");
let modal = document.querySelector("#modal");
let log=document.querySelector("#log");

open.onclick = () => {
    modal.style.display = "flex";
};

close.onclick = () => {
    modal.style.display = "none";
};

