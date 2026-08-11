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

log.onclick=()=>{
    let name=document.querySelector("#name").value;
    let email=document.querySelector("#mail").value;
    let phone=document.querySelector("#phone").value;

    if(name==="" || email==="" || phone===""){
        alert("Fill all required details");
    }
    else{
        alert("Successfully added");
        modal.style.display="none";
    }
}