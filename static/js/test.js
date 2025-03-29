document.addEventListener("DOMContentLoaded", function () {
    updateFilters();
});

function updateFilters() {
    let program = document.getElementById("program");
    let discipline = document.getElementById("discipline");
    let level = document.getElementById("level");
    let subject = document.getElementById("subject");
    let chapter = document.getElementById("chapter");

    discipline.disabled = program.value === "";
    level.disabled = discipline.value === "";
    subject.disabled = level.value === "";
    chapter.disabled = subject.value === "";
}

function clearFilters() {
    document.getElementById("program").value = "";
    document.getElementById("discipline").value = "";
    document.getElementById("level").value = "";
    document.getElementById("subject").value = "";
    document.getElementById("chapter").value = "";

    updateFilters();
}
