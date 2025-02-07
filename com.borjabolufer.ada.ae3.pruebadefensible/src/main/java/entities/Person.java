package entities;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

@Entity
@Table(name = "person_bb04")
public class Person {
	@Id
	@Column(name = "DRIVER_ID", length=50)
	private String driverID;
	@Column(name = "ADDRESS", length=50)
	private String address;
	@Column(name = "name", length=50)
	private String name;
	
	@OneToMany(mappedBy = "person", cascade = CascadeType.REMOVE)
	private Set<Car> cars = new HashSet<Car>();

	public Person() {
	}
	

	public Person(String driverID, String address, String name, Set<Car> cars) {
		super();
		this.driverID = driverID;
		this.address = address;
		this.name = name;
		this.cars = cars;
	}


	//TODO metodo publico añadir coche
	public void addCar(Car car) {
		if(car == null) {
			return;
		}
		
		this.cars.add(car);
		
		if (car.getPerson() != this) {
			car.setPerson(this);
		}
	}
	
	public void removeCar(Car car) {
	    if (car == null) {
	        return;
	    }
	    
	    this.cars.remove(car);
	    
	    if (car.getPerson() == this) {
	        car.setPerson(null);
	    }
	}
	
	public String getDriverID() {
		return driverID;
	}

	public void setDriverID(String driverID) {
		this.driverID = driverID;
	}

	public String getAddress() {
		return address;
	}

	public void setAddress(String address) {
		this.address = address;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Set<Car> getCars() {
		return cars;
	}

	public void setCars(Set<Car> cars) {
		this.cars = cars;
	}

	@Override
	public String toString() {
		return "Person [driverID=" + driverID + ", address=" + address + ", name=" + name + ", cars=" + cars + "]";
	}


	@Override
	public int hashCode() {
		return Objects.hash(address, cars, driverID, name);
	}


	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Person other = (Person) obj;
		return Objects.equals(address, other.address) && Objects.equals(cars, other.cars)
				&& Objects.equals(driverID, other.driverID) && Objects.equals(name, other.name);
	}



}
