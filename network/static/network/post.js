document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    document.querySelectorAll('.heart').forEach(heart => {
        heart.addEventListener('click', event => liketoggle(event, csrftoken))
    })
    document.querySelectorAll('.post').forEach(post => {
        update_likes(post_id, csrftoken)
    })

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
            if (like.liked) {
                fetch(`/likeapi/${postid}`, {
                    method: 'PUT',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        liked: true
                    })
                })
            } else {
                fetch(`/likeapi/${postid}`, {
                    method: 'PUT',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        liked: false
                    })
                })
            }
        })
        .then(() => update_likes(postid, csrftoken))
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
            if (liked) {
                let heart = document.getElementById(`heart${post_id}`).getElementsByClassName(`icon`)
                heart.fill = "red"
            }
        })
}