document.addEventListener("DOMContentLoaded", () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    document.querySelectorAll('.heart').forEach(heart => {
        heart.addEventListener('click', event => liketoggle(event, csrftoken))
    })
    document.querySelectorAll('.post').forEach(post => {
        let id = post.id
        update_likes(id, csrftoken)
    })
    document.querySelectorAll('.editform').forEach(post => {
        post.onsubmit = event => {
            event.preventDefault()
            editpost(event, csrftoken)
            return false
        }
    })
    document.querySelectorAll('.editbutton').forEach(button => {
        button.addEventListener('click', event => toggleedit(event))
    })
    document.querySelectorAll('.deletebutton').forEach(button => {
        button.addEventListener('click', event => deletepost(event, csrftoken))
    })
    if (document.querySelector('.follow')) {
        followBtn = document.querySelector('.follow')
        followBtn.addEventListener('click', event => followToggle(event, csrftoken))
        try {
            followid = parseInt(followBtn.id.slice(6))
        } catch (error) {
            console.log(error)
        }
        update_follow(followid, csrftoken)
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
            var root = document.querySelector(':root');
            var rootStyles = getComputedStyle(root);
            var primary = rootStyles.getPropertyValue('--bs-primary');
            if (liked) {
                heartsvg.style.color = "red"
            } else {
                heartsvg.style.color = primary
            }
        })
}

function followToggle(event, csrftoken) {
    let followid = event.target.id
    try {
        followid = parseInt(followid.slice(6))
    } catch (error) {
        console.log(error)
    }

    // check follow status via api
    fetch(`/followapi/${followid}`, {
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        // change like status via api
        .then(follow => {
            fetch(`/followapi/${followid}`, {
                    method: 'PUT',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({
                        following: follow.follow
                    })
                })
                .then(() => update_follow(followid, csrftoken))
        })

}

// change follow/unfollow button appearance based on current status
function update_follow(follow_id, csrftoken) {
    fetch(`/followapi/${follow_id}`, {
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => response.json())
        // change like status via api
        .then(follow => {
            let user_following = follow.follow
            let following = follow.following
            let followers = follow.followers
            let button = document.getElementById(`follow${follow_id}`)
            let followersCount = document.getElementById(`followers${follow_id}`)
            let followingCount = document.getElementById(`following${follow_id}`)
            followersCount.innerHTML = followers
            followingCount.innerHTML = following
            if (user_following) {
                button.innerHTML = "Unfollow"
                button.classList.remove("btn-primary")
                button.classList.add("btn-secondary")
            } else {
                button.innerHTML = "Follow"
                button.classList.add("btn-primary")
                button.classList.remove("btn-secondary")
            }
        })
}


function editpost(event, csrftoken) {
    console.log(event)
    event.preventDefault()
    let form = event.target
    let posttextbox = form.children[0]
    console.log(posttextbox)
    let posttext = posttextbox.value
    fetch(`/editapi`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                post_id: postid,
                posttext: posttext
            })
        })
        .then(response => response.json())
        // remove html div for post
        .then(data => {
            let post_id = data.post_id
            posttext = document.getElementById(`posttext${post_id}`)
            posttext.innerHTML = data.post_text
            edited = document.getElementById(`edited${post_id}`)
            edited.innerHTML = "Edited"
        })
    return false
}

function toggleedit(event) {
    let posteditid = event.target.id
    try {
        postid = parseInt(posteditid.slice(4))
    } catch (error) {
        console.log(error)
    }
    postdiv = document.getElementById(`editform${postid}`)
    if (postdiv.style.display === "none") {
        postdiv.style.display = "block"
    } else {
        postdiv.style.display = "none"
    }
}


function deletepost(event, csrftoken) {
    let deletebuttonid = event.target.id
    try {
        postid = parseInt(deletebuttonid.slice(6))
    } catch (error) {
        console.log(error)
    }
    fetch(`/editapi`, {
            method: 'PUT',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({
                post_id: postid
            })

        })
        .then(response => response.json())
        // remove html div for post
        .then(deletejson => {
            let post_id_delete = deletejson['deleted']
            post = document.getElementById(`post${post_id_delete}`)
            post.remove()
        })
}