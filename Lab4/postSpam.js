const WPAPI = require('wpapi')

const wp = new WPAPI({
    endpoint: 'http://localhost/wp-json',
    username: 'wordpressuser123',
    password: 'password123',
    auth: true
})

let createPost = () => {
    wp.posts().create({
        title: 'I just found some cryptocurrency',
        content: 'Press here: <a href="http://localhost">http://localhost</a>',
        status: 'publish'
    }).then((response) => {
        console.log(response.id)
    }).catch(error => {
        console.log(error)
    })
}

createPost()