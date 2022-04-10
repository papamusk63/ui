import { useState } from 'react'

export const Dropdown = (props) => {
  const { items, title, icon, instance, handleClick, isActive, subInstance } = props;
  const [isOpen, setOpen] = useState(false);
  const toggleDropdown = () => setOpen(!isOpen);
  
  return (
    <div className='hunter-dropdown'>
      <div className='hunter-dropdown-header' onClick={toggleDropdown}>
        <i className={icon} />
        {title}
        <i className={`fa fa-chevron-right hunter-dropdown-icon icon ${isOpen && "open"}`}></i>
      </div>
      <div className={`hunter-dropdown-body ${isOpen && 'open'}`}>
        {items.map(item => (
          <div className={`hunter-dropdown-item ${isActive && item.instance === subInstance && 'hunter-selected'}`}
            onClick={e => {
              handleClick(instance, item.pathname)
            }}
            id={item.id}
            key={`${instance}-${item.id}`}
          >
            {item.label}
          </div>
        ))}
      </div>
    </div>
  )
}