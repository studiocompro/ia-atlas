(function(){
function get(key){try{return JSON.parse(localStorage.getItem(key)||'[]')}catch(e){return[]}}
function put(key,x){localStorage.setItem(key,JSON.stringify([...new Set(x)]))}
function sync(){const f=get('iaAtlasFavs');document.querySelectorAll('.favbtn').forEach(b=>{const on=f.includes(b.dataset.id);b.classList.toggle('active',on);b.textContent=on?'★ Favori':'☆ Ajouter aux favoris'})}
document.addEventListener('click',e=>{const b=e.target.closest('.favbtn');if(b){let f=get('iaAtlasFavs'),id=b.dataset.id;f=f.includes(id)?f.filter(x=>x!==id):[...f,id];put('iaAtlasFavs',f);sync()}const c=e.target.closest('.addcompare');if(c){let x=get('iaAtlasCompare');if(!x.includes(c.dataset.id)&&x.length<4)x.push(c.dataset.id);put('iaAtlasCompare',x);c.textContent='Ajouté ✓'}});sync();
})();