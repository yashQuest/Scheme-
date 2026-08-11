let open = document.querySelector("#openBtn");
let close = document.querySelector("#closeBtn");
let modal = document.querySelector("#modal");
let log = document.querySelector("#log");
let search = document.querySelector("#search");

let contacts = [];
let editIndex = -1;

// Open Modal
open.onclick = () => {
    modal.style.display = "flex";
};

// Close Modal
close.onclick = () => {
    modal.style.display = "none";

    document.querySelector("#name").value = "";
    document.querySelector("#mail").value = "";
    document.querySelector("#phone").value = "";
    document.querySelector("#company").value = "";

    editIndex = -1;
    log.innerText = "Add";
};

// Display Contacts
function display() {

    let container = document.querySelector("#cardcontainer");
    let card = "";

    contacts.forEach((val, idx) => {

        card += `
        <div class="card data m-3" style="width:18rem;">

            <img src="${val.Photo}" class="card-img-top" style="height:220px; object-fit:cover;">

            <div class="card-body">

                <h5>${val.Name}</h5>

                <p><b>Email:</b> ${val.Email}</p>

                <p><b>Phone:</b> ${val.PhoneNumber}</p>

                <p><b>Company:</b> ${val.Company}</p>

                <button class="btn btn-danger btn-sm"
                    onclick="DeleteCard(${idx})">
                    Delete
                </button>

                <button class="btn btn-primary btn-sm"
                    onclick="EditCard(${idx})">
                    Edit
                </button>

                <button class="btn btn-success btn-sm"
                    onclick="document.getElementById('photo${idx}').click()">
                    Update Photo
                </button>

                <input
                    type="file"
                    id="photo${idx}"
                    accept="image/*"
                    hidden
                    onchange="UpdatePhoto(event,${idx})">

            </div>

        </div>
        `;
    });

    container.innerHTML = card;
}

// Add / Update Contact

log.onclick = () => {

    let name = document.querySelector("#name").value.trim();
    let email = document.querySelector("#mail").value.trim();
    let phone = document.querySelector("#phone").value.trim();
    let company = document.querySelector("#company").value.trim();

    if (name === "" || email === "" || phone === "") {
        alert("Please fill all required fields.");
        return;
    }

    let contact = {

        Name: name,
        Email: email,
        PhoneNumber: phone,
        Company: company,
        Photo: "Default.jpeg"

    };

    if (editIndex === -1) {

        contacts.push(contact);

    } else {

        contact.Photo = contacts[editIndex].Photo;

        contacts[editIndex] = contact;

        editIndex = -1;

        log.innerText = "Add";
    }

    display();

    modal.style.display = "none";

    document.querySelector("#name").value = "";
    document.querySelector("#mail").value = "";
    document.querySelector("#phone").value = "";
    document.querySelector("#company").value = "";

};

// Delete Contact

function DeleteCard(index) {

    if (confirm("Delete this contact?")) {

        contacts.splice(index, 1);

        display();
    }

}

// Edit Contact

function EditCard(index) {

    document.querySelector("#name").value =
        contacts[index].Name;

    document.querySelector("#mail").value =
        contacts[index].Email;

    document.querySelector("#phone").value =
        contacts[index].PhoneNumber;

    document.querySelector("#company").value =
        contacts[index].Company;

    editIndex = index;

    log.innerText = "Update";

    modal.style.display = "flex";

}

// Search Contact

search.onclick = () => {

    let text = document
        .querySelector("#data")
        .value
        .trim()
        .toLowerCase();

    if (text === "") {

        alert("Enter a name to search.");

        return;
    }

    let found = false;

    contacts.forEach((val) => {

        if (val.Name.toLowerCase() === text) {

            found = true;

            alert(
`Name : ${val.Name}

Email : ${val.Email}

Phone : ${val.PhoneNumber}

Company : ${val.Company}`
            );

        }

    });

    if (!found) {

        alert("Contact not found.");

    }

};

// Update Photo

function UpdatePhoto(event, index) {

    let file = event.target.files[0];

    if (!file) return;

    let reader = new FileReader();

    reader.onload = function () {

        contacts[index].Photo = reader.result;

        display();

    };

    reader.readAsDataURL(file);

}