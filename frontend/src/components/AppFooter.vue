<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-row">
        <div class="footer-column">
          <h3>О компании</h3>
          <p>Интернет-магазин электроники с широким выбором товаров и доступными ценами. Быстрая доставка по всей России.</p>
          <div class="social-icons">
            <a href="#" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
            <a href="#" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
            <a href="#" aria-label="Twitter"><i class="fab fa-twitter"></i></a>
            <a href="#" aria-label="YouTube"><i class="fab fa-youtube"></i></a>
          </div>
        </div>
        
        <div class="footer-column">
          <h3>Навигация</h3>
          <ul class="footer-links">
            <li><router-link to="/">Главная</router-link></li>
            <li><router-link to="/catalog">Каталог</router-link></li>
            <li><router-link to="/promotions">Акции</router-link></li>
            <li><router-link to="/about">О нас</router-link></li>
            <li><router-link to="/delivery">Доставка и оплата</router-link></li>
          </ul>
        </div>
        
        <div class="footer-column">
          <h3>Покупателям</h3>
          <ul class="footer-links">
            <li><router-link to="/how-to-order">Как сделать заказ</router-link></li>
            <li><router-link to="/faq">Вопросы и ответы</router-link></li>
            <li><router-link to="/returns">Возврат товара</router-link></li>
            <li><router-link to="/warranty">Гарантия</router-link></li>
            <li><router-link to="/contacts">Контакты</router-link></li>
          </ul>
        </div>
        
        <div class="footer-column">
          <h3>Контакты</h3>
          <ul class="contact-info">
            <li><i class="fas fa-map-marker-alt"></i> г. Москва, ул. Примерная, 123</li>
            <li><i class="fas fa-phone-alt"></i> 8 (800) 123-45-67</li>
            <li><i class="fas fa-envelope"></i> info@example.ru</li>
            <li><i class="fas fa-clock"></i> Пн-Пт: 9:00-20:00, Сб-Вс: 10:00-18:00</li>
          </ul>
        </div>
      </div>
      
      <div class="footer-row subscribe">
        <div class="footer-column full-width">
          <h3>Подпишитесь на рассылку</h3>
          <p>Получайте информацию о новых товарах и скидках первыми</p>
          <div class="subscribe-form">
            <input type="email" placeholder="Введите ваш e-mail" aria-label="Email для подписки" />
            <button type="submit">Подписаться</button>
          </div>
        </div>
      </div>
      
      <div class="footer-row payment-methods">
        <div class="footer-column full-width">
          <h3>Способы оплаты</h3>
          <div class="payment-icons">
            <span class="payment-icon"><i class="fab fa-cc-visa"></i> Visa</span>
            <span class="payment-icon"><i class="fab fa-cc-mastercard"></i> MasterCard</span>
            <span class="payment-icon"><i class="fab fa-cc-paypal"></i> PayPal</span>
            <span class="payment-icon"><i class="fas fa-credit-card"></i> Mir</span>
            <span class="payment-icon"><i class="fas fa-money-bill-wave"></i> Наличные</span>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="copyright">
          © 2024 Название компании. Все права защищены.
        </div>
        <div class="legal-links">
          <router-link to="/terms">Условия использования</router-link>
          <router-link to="/privacy">Политика конфиденциальности</router-link>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
  color: #ffffff;
  padding: 40px 0 20px;
  margin-top: 50px;
  font-size: 1.4rem;
  box-shadow: 0 -5px 15px rgba(0, 0, 0, 0.1);
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-row {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.footer-column {
  flex: 1 0 250px;
  margin-bottom: 20px;
  padding: 0 15px;
  transition: transform 0.3s ease;
}

.footer-column:hover {

}

.full-width {
  flex: 1 0 100%;
}

.footer h3 {
  color: #ffffff;
  font-size: 1.8rem;
  margin-bottom: 20px;
  position: relative;
  font-weight: 600;
}

.footer h3::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -8px;
  width: 40px;
  height: 2px;
  background: linear-gradient(90deg, #6b46c1 0%, #805ad5 100%);
  border-radius: 2px;
}

.footer p {
  line-height: 1.6;
  margin-bottom: 20px;
  color: #e2e8f0;
}

.social-icons {
  display: flex;
  gap: 12px;
}

.social-icons a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: #ffffff;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.social-icons a:before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.social-icons a:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(107, 70, 193, 0.3);
}

.social-icons a:hover:before {
  opacity: 1;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 10px;
  transition: transform 0.3s ease;
}

.footer-links li:hover {
  transform: translateX(5px);
}

.footer-links a {
  color: #e2e8f0;
  text-decoration: none;
  transition: color 0.3s;
  display: inline-block;
  padding: 3px 0;
  position: relative;
}

.footer-links a:after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: linear-gradient(90deg, #6b46c1 0%, #805ad5 100%);
  transition: width 0.3s ease;
}

.footer-links a:hover {
  color: #ffffff;
}

.footer-links a:hover:after {
  width: 100%;
}

.contact-info {
  list-style: none;
  padding: 0;
  margin: 0;
}

.contact-info li {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
  color: #e2e8f0;
  transition: transform 0.3s ease;
}

.contact-info li:hover {
  transform: translateX(5px);
}

.contact-info li i {
  margin-right: 10px;
  color: #805ad5;
  transition: color 0.3s;
}

.contact-info li:hover i {
  color: #6b46c1;
}

.subscribe {
  background: linear-gradient(135deg, rgba(107, 70, 193, 0.1) 0%, rgba(128, 90, 213, 0.15) 100%);
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.subscribe-form {
  display: flex;
  gap: 10px;
  max-width: 500px;
}

.subscribe-form input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  color: #ffffff;
  font-size: 1.4rem;
  transition: all 0.3s ease;
}

.subscribe-form input:focus {
  border-color: #6b46c1;
  outline: none;
  box-shadow: 0 0 0 2px rgba(107, 70, 193, 0.2);
}

.subscribe-form input::placeholder {
  color: #a0aec0;
}

.subscribe-form button {
  padding: 12px 20px;
  background: linear-gradient(90deg, #6b46c1 0%, #805ad5 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  box-shadow: 0 4px 6px rgba(107, 70, 193, 0.2);
}

.subscribe-form button:hover {
  background: linear-gradient(90deg, #805ad5 0%, #6b46c1 100%);
  box-shadow: 0 6px 10px rgba(107, 70, 193, 0.3);
}

.payment-methods {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
}

.payment-icons {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.payment-icon {
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 20px;
  border-radius: 8px;
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.payment-icon i {
  font-size: 1.8rem;
  color: #805ad5;
}

.payment-icon:hover {
  background: rgba(107, 70, 193, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
}

.footer-bottom {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: 20px;
  font-size: 1.3rem;
}

.copyright {
  color: #a0aec0;
  margin-bottom: 10px;
}

.legal-links {
  display: flex;
  gap: 20px;
}

.legal-links a {
  color: #a0aec0;
  text-decoration: none;
  transition: all 0.3s;
  position: relative;
}

.legal-links a:after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: linear-gradient(90deg, #6b46c1 0%, #805ad5 100%);
  transition: width 0.3s ease;
}

.legal-links a:hover {
  color: #ffffff;
}

.legal-links a:hover:after {
  width: 100%;
}

@media (max-width: 992px) {
  .footer-column {
    flex: 1 0 50%;
  }
}

@media (max-width: 768px) {
  .footer-row {
    flex-direction: column;
  }
  
  .footer-column {
    flex: 1 0 100%;
  }
  
  .subscribe-form {
    flex-direction: column;
  }
  
  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
  
  .legal-links {
    margin-top: 15px;
    justify-content: center;
  }
}
</style>

<script setup>
// Компонент футера не требует дополнительной логики
</script> 