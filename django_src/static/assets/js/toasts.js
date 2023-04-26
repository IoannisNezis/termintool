function toastHTML(tag, text) {
    return `<div class="toast align-items-center text-bg-${tag} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${text}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>`
}

function createDOMElement(tag, text) {
    const template = document.createElement("toast");
    template.innerHTML = toastHTML(tag, text).trim()
    return template.firstChild;

}

function createToast(tag, text, path) {
    const toastContainer = document.getElementById("toast-container")
    const domElement = createDOMElement(tag, text, path);
    toastContainer.appendChild(domElement);
    const toast = new bootstrap.Toast(domElement);
    toast.show();

}

function create_message_toast(tag, text) {
    createToast(tag, text);
}
