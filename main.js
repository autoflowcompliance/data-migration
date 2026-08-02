// ── Mobile menu toggle ──
function toggleMenu(){
  document.getElementById('mobile-nav').classList.toggle('open');
}

// ── Scroll reveal for sticky CTA ──
window.addEventListener('scroll',()=>{
  const heroTicker=document.querySelector('.hero-ticker');
  const stickyBtn=document.getElementById('sticky-cta');
  if(heroTicker){
    const rect=heroTicker.getBoundingClientRect();
    stickyBtn.classList.toggle('show',rect.bottom<window.innerHeight);
  }
});

// ── Active nav link highlighting ──
function setActiveNavLink(){
  const currentPage=window.location.pathname.split('/').pop() || 'index.html';
  const navLinks=document.querySelectorAll('.nav-links a');
  navLinks.forEach(link=>{
    const linkPage=link.getAttribute('href');
    if(linkPage===currentPage || (currentPage==='' && linkPage==='index.html')){
      link.classList.add('active');
    }else{
      link.classList.remove('active');
    }
  });
}

document.addEventListener('DOMContentLoaded',setActiveNavLink);

// ── Lawsuit ticker animation ──
function animateTicker(){
  const tickerNum=document.getElementById('ticker-num');
  if(!tickerNum)return;
  
  let current=3948;
  const target=5100;
  const duration=2000;
  const increment=(target-current)/(duration/16);
  let count=current;
  
  const timer=setInterval(()=>{
    count+=increment;
    if(count>=target){
      tickerNum.textContent='5,100+';
      clearInterval(timer);
      // Start 18-second increment
      setInterval(()=>{
        const currentVal=parseInt(tickerNum.textContent.replace(/[^0-9]/g,''))||5100;
        tickerNum.textContent=(currentVal+1).toLocaleString()+'+';
      },18000);
    }else{
      tickerNum.textContent=Math.floor(count).toLocaleString()+'+';
    }
  },16);
}

document.addEventListener('DOMContentLoaded',animateTicker);

// ── FAQ accordion toggle ──
function toggleFaq(id){
  const faqItem=document.getElementById(id);
  faqItem.classList.toggle('expanded');
}

// ── How It Works card toggle ──
function toggleHowCard(id){
  const card=document.getElementById(id);
  card.classList.toggle('expanded');
}

// ── Case study card toggle ──
function toggleCaseStudy(id){
  const card=document.getElementById(id);
  card.classList.toggle('expanded');
}

// ── About feature card toggle ──
function toggleAboutFeature(id){
  const card=document.getElementById(id);
  card.classList.toggle('expanded');
}

// ── CTA band form submission ──
function submitCtaBandForm(event){
  event.preventDefault();
  const url=document.getElementById('cta-band-url').value.trim();
  if(url){
    window.location.href=`scan.html?url=${encodeURIComponent(url)}`;
  }
}

// ── Contact form submission ──
function submitContactForm(event){
  event.preventDefault();
  const form=event.target;
  const firstName=form.querySelector('[name="first"]').value.trim();
  const email=form.querySelector('[name="email"]').value.trim();
  
  if(!firstName || !email){
    alert('Please fill in your name and email.');
    return;
  }
  
  form.innerHTML=`
    <div style="text-align:center;padding:48px 0">
      <div style="font-size:48px;margin-bottom:16px">✅</div>
      <h3 style="font-family:var(--serif);font-size:24px;font-weight:700;color:var(--ink);margin-bottom:8px">Got it, ${firstName}.</h3>
      <p style="font-size:15px;color:var(--ink-light);line-height:1.8">We'll be in touch at <strong style="color:var(--ink)">${email}</strong> within 24 hours.</p>
      <p style="font-size:14px;color:var(--ink-light);margin-top:16px">Also feel free to email us directly at <a href="mailto:autoflowcompliance@outlook.com" style="color:var(--cobalt)">autoflowcompliance@outlook.com</a></p>
    </div>
  `;
}

// ── Partner form submission ──
function submitPartnerForm(event){
  event.preventDefault();
  const form=event.target;
  const firstName=form.querySelector('[name="first"]').value.trim();
  const email=form.querySelector('[name="email"]').value.trim();
  
  if(!firstName || !email){
    alert('Please fill in your name and email.');
    return;
  }
  
  form.innerHTML=`
    <div style="text-align:center;padding:48px 0">
      <div style="font-size:48px;margin-bottom:16px">✅</div>
      <h3 style="font-family:var(--serif);font-size:24px;font-weight:700;color:var(--ink);margin-bottom:8px">Message received, ${firstName}.</h3>
      <p style="font-size:15px;color:var(--ink-light);line-height:1.8">We'll be in touch at <strong style="color:var(--ink)">${email}</strong> within 24 hours.</p>
      <p style="font-size:14px;color:var(--ink-light);margin-top:16px">Referral fee: £400–£500 per converted introduction.</p>
    </div>
  `;
}

// ── Scroll reveal animations ──
const observerOptions={
  threshold:0.1,
  rootMargin:'0px 0px -50px 0px'
};

const observer=new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      entry.target.style.animationPlayState='running';
      observer.unobserve(entry.target);
    }
  });
},observerOptions);

document.addEventListener('DOMContentLoaded',()=>{
  const animatedElements=document.querySelectorAll('[style*="animation"]');
  animatedElements.forEach(el=>{
    el.style.animationPlayState='paused';
    observer.observe(el);
  });
});

// ── Stats counter animation ──
function animateCounter(element,target,duration=2000){
  const start=0;
  const increment=target/(duration/16);
  let current=start;
  
  const timer=setInterval(()=>{
    current+=increment;
    if(current>=target){
      element.textContent=target.toLocaleString();
      clearInterval(timer);
    }else{
      element.textContent=Math.floor(current).toLocaleString();
    }
  },16);
}

// ── Initialize counter animations on scroll ──
const counterObserver=new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      const target=parseInt(entry.target.textContent.replace(/[^0-9]/g,''));
      animateCounter(entry.target,target);
      counterObserver.unobserve(entry.target);
    }
  });
},{threshold:0.5});

document.addEventListener('DOMContentLoaded',()=>{
  const counters=document.querySelectorAll('.stat-bar-number,.about-stat-num,.trust-number');
  counters.forEach(counter=>counterObserver.observe(counter));
});
