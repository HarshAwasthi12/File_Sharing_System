function toggleDark(){
    document.body.classList.toggle("dark");
}

function deleteFile(filename){
    fetch('/delete/' + filename)
    .then(() => location.reload());
}

function searchFile() {
    let input = document.getElementById("search").value.toLowerCase();
    let rows = document.querySelectorAll("table tr");

    rows.forEach((row, index) => {
        if(index === 0) return;
        let text = row.innerText.toLowerCase();
        row.style.display = text.includes(input) ? "" : "none";
    });
}

document.getElementById('uploadForm').addEventListener('submit', function(e){
    e.preventDefault();
    const file = document.getElementById('fileInput').files[0];
    const formData = new FormData();
    formData.append('file', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    xhr.onload = function(){
        location.reload();
    };

    xhr.send(formData);
});