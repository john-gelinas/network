document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    document.querySelectorAll('.heart').forEach(heart => {
        heart.addEventListener('click', event => liketoggle(event, csrftoken))
    })
    document.querySelectorAll('.post').forEach(post => {
        let id = post.id
        update_likes(id, csrftoken)
    })
    if (document.querySelector('#follower')) {
        followBtn = document.querySelector('#follower')
        followBtn.addEventListener('click', event => followToggle(event, csrftoken))
    }
})


function liketoggle(event, csrftoken) {
    let heartid = event.target.id
    try {
        postid = parseInt(heartid.slice(5))
    } catch (error) {
        console.log(error)
    }
    // check like status via api
    fetch(`/likeapi/${postid}`, {
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        // change like status via api
        .then(like => {
            fetch(`/likeapi/${postid}`, {
                    method: 'PUT',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        liked: like.liked
                    })
                })
                .then(() => update_likes(postid, csrftoken))
        })

}

// change like button appearance and like count based on current status
function update_likes(post_id, csrftoken) {
    fetch(`/likeapi/${post_id}`, {
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        // change like status via api
        .then(like => {
            let totalLikes = like.total_likes
            let liked = like.liked
            likes_counter = document.querySelector(`#likes${post_id}`)
            likes_counter.innerHTML = `${totalLikes}`
            let heartsvg = document.getElementById(`heart${post_id}`)
            if (liked) {
                heartsvg.style.color = "red"
            } else {
                heartsvg.style.color = "black"
            }
        })
}

function followToggle(event, csrftoken) {
    let followid = event.target.id
    
}