import styles from "../styles/Message.module.css";

export default function Message({ role, text }) {
  return (
    <div className={`${styles.message} ${styles[role]}`}>
      {text}
    </div>
  );
}
