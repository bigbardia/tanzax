let form = document.querySelector("form");
let btn = document.getElementById("button");
let p = document.getElementById("payam");
let file = document.getElementById("file_selector");
file.onchange = ()=>{
        if (file.files.length > 0) {
            let file_size =    file.files[0].size;
            if (file_size > 20 * 1000 * 1000) {
                p.innerText = "فایل بزرگ است";
            }
            
            else  {
                p.innerText = "";
            }
    }
}

btn.onclick = ()=>{


    if (file.files.length > 0) {
        let file_size= file.files[0].size;

        if (file_size <= 20 * 1000 * 1000){
            form.submit();
        }
        
        else {
            p.innerText = "فایل بزرگ است"
        }
    }
    else {
        
        form.submit();
    }
}