document.addEventListener("DOMContentLoaded", function () {
    const profileForm = document.getElementById("profile-form");
    const editButton = document.getElementById("edit-profile");
    const saveButton = document.getElementById("save-profile");
    const cancelButton = document.getElementById("cancel-edit");

    const programSelect = document.getElementById("program_id");
    const disciplineSelect = document.getElementById("discipline_id");
    const levelSelect = document.getElementById("level_id");

    const profilePic = document.getElementById("profile-pic");
    const uploadPicInput = document.getElementById("upload-pic");
    const deletePicButton = document.getElementById("delete-profile-pic");

    let originalData = {}; // Store original values for cancel action

    function storeOriginalData() {
        originalData = {};
        profileForm.querySelectorAll("input, select").forEach(field => {
            originalData[field.name] = field.value;
        });
    }

    storeOriginalData(); // Store original values on page load

    editButton.addEventListener("click", function () {
        profileForm.querySelectorAll("input, select").forEach(field => {
            field.disabled = false;
        });
        saveButton.style.display = "inline-block";
        cancelButton.style.display = "inline-block";
        editButton.style.display = "none";
    });

    cancelButton.addEventListener("click", function () {
        profileForm.querySelectorAll("input, select").forEach(field => {
            field.disabled = true;
            field.value = originalData[field.name];
        });
        saveButton.style.display = "none";
        cancelButton.style.display = "none";
        editButton.style.display = "inline-block";
    });

    profileForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(profileForm);
        fetch("/update_profile", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showFlashMessage(data.message, data.category);
            profileForm.querySelectorAll("input, select").forEach(field => {
                field.disabled = true;
            });
            setTimeout(() => location.reload(), 2000);
            } else {
                showFlashMessage(data.message, data.category);
            }
        });
    });

    programSelect.addEventListener("change", function () {
        fetch(`/get_disciplines/${this.value}`)
            .then(response => response.json())
            .then(data => {
                disciplineSelect.innerHTML = '<option value="">Select Discipline</option>';
                data.forEach(discipline => {
                    let option = document.createElement("option");
                    option.value = discipline.id;
                    option.textContent = discipline.name;
                    disciplineSelect.appendChild(option);
                });
                disciplineSelect.disabled = data.length === 0;
            });
    });

    disciplineSelect.addEventListener("change", function () {
        fetch(`/get_levels/${this.value}`)
            .then(response => response.json())
            .then(data => {
                levelSelect.innerHTML = '<option value="">Select Level</option>';
                data.forEach(level => {
                    let option = document.createElement("option");
                    option.value = level.id;
                    option.textContent = level.name;
                    levelSelect.appendChild(option);
                });
                levelSelect.disabled = data.length === 0;
            });
    });

    // ✅ Profile Picture Upload (Instant Update)
    uploadPicInput.addEventListener("change", function () {
        const formData = new FormData();
        formData.append("profile_pic", uploadPicInput.files[0]);

        fetch("/upload_profile_pic", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                profilePic.src = data.image_url + "?t=" + new Date().getTime();
                showFlashMessage(data.message, data.category);
            } else {
                showFlashMessage(data.message, data.category);
            }
        });
    });

    // ✅ Delete Profile Picture (Instant Update)
    deletePicButton.addEventListener("click", function () {
        fetch("/delete_profile_pic", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                profilePic.src = "/static/images/default_pic.jpg?t=" + new Date().getTime();
                showFlashMessage(data.message, data.category);
            } else {
                showFlashMessage(data.message, data.category);
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        document.querySelectorAll('.flash-messages .alert').forEach(alert => {
            alert.style.transition = "opacity 0.5s ease-out";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
});

function showFlashMessage(message, category) {
    const flashMessagesContainer = document.getElementById("flash-messages");
    if (!flashMessagesContainer) return;

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
    alertDiv.setAttribute("role", "alert");

    const iconHTML = category === 'success' ? '<i class="bi bi-check-circle-fill me-2"></i>' :
                    category === 'error' ? '<i class="bi bi-exclamation-circle-fill me-2"></i>' :
                    category === 'info' ? '<i class="bi bi-info-circle-fill me-2"></i>' :
                    category === 'warning' ? '<i class="bi bi-exclamation-triangle-fill me-2"></i>' : '';

    alertDiv.innerHTML = `${iconHTML} ${message}`;

    flashMessagesContainer.appendChild(alertDiv);

    // Auto-fade out after 5 seconds
    setTimeout(() => {
        alertDiv.style.transition = "opacity 0.5s ease-out";
        alertDiv.style.opacity = "0";
        setTimeout(() => alertDiv.remove(), 500);
    }, 5000);
}
