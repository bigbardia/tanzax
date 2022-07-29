function Like(_id){
    let csrf_token = document.getElementById("csrf_token").value

    $.ajax({
    method : "POST",
    headers : {
        "X-CSRFToken" : csrf_token,
        "Cookie" : document.cookie,
    },
    url : "/like_posts",
    data  : {
        "post_id" : _id,
    },
    success :  resp =>{
        let likes = resp.likes;
        let like_button = document.getElementById(parseInt(_id));
        like_button.innerText = likes;
    }

    })
}