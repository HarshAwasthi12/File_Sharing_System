const form = document.getElementById('uploadForm');
const progressBar = document.getElementById('progressBar');
const progressBox = document.getElementById('progressBox');

form.addEventListener('submit', function(e){
    e.preventDefault();
    const file = document.getElementById('fileInput').files[0];
    const formData = new FormData();
    formData.append('file', file);

    progressBox.style.display = 'block';

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    xhr.upload.onprogress = function(e){
        if(e.lengthComputable){
            const percent = (e.loaded / e.total) * 100;
            progressBar.style.width = percent + '%';
        }
    };

    xhr.onload = function(){
        location.reload();
    };

    xhr.send(formData);
});

function deleteFile(filename){
    fetch('/delete/' + filename)
    .then(() => location.reload());
}