function loadFile(input) {
    let file = input.files[0];

    let newImage = document.createElement("img");

    newImage.src = URL.createObjectURL(file);
    newImage.style.width = "100%";
    newImage.style.height = "100%";
    newImage.style.objectFit = "cover";

    let container = document.getElementById('image-show');
    container.appendChild(newImage);
}