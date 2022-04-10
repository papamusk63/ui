export function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

// export function validateEmail(email) {
//  if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(email))
//   {
//     return (true)
//   }
//     alert("You have entered an invalid email address!")
//     return (false)
// }

export function currentDateString() {
    const date = new Date();
    let month = date.getMonth() + 1
    let day = date.getDate()
    if (date.getMonth() + 1 < 10) {
        month = '0' + month
    }
    if (date.getDate() < 10) {
        day = '0' + day
    }

    return `${date.getFullYear()}-${month}-${day}`;
}