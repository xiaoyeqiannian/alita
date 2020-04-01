
function GET(params) {
  const p = new Promise((resolve, reject) => {
    $.ajax({
        url: params.url,
        type: 'get',
        dataType: 'json',
        data: params.data || {}, 
        timeout: 5000,
        success: function (result) {
            if (result.code == "0000") {
                resolve(result.data);
            } else {
                reject(new Error(result.data))
            }   
        },  
        error: function () {
            reject(new Error('服务器异常'))
        }   
    })  
  })  
  return p
}
function POST(params) {
  const p = new Promise((resolve, reject) => {
    $.ajax({
        url: params.url,
        type: 'post',
        dataType: 'json',
        data: params.data || {}, 
        timeout: 5000,
        success: function (result) {
            if (result.code == "0000") {
                resolve(result.data);
            } else {
                reject(new Error(result.data))
            }   
        },  
        error: function () {
            reject(new Error('服务器异常'))
        }   
    })  
  })  
  return p
}

