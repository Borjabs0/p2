package entities;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "car_bb04")
public class Car {
	@Id
	@Column(name = "LICENSE_ID", length = 50)
	private String licenseID;

	@Column(name = "MODEL", length = 50)
	private String model;

	@Column(name = "YEAR")
	private Integer year;

	@ManyToOne
	@JoinColumn(name = "DRIVER_ID", nullable = false)
	private Person person;

	@OneToOne(mappedBy = "car")
	private Policy policy;

	@ManyToMany(mappedBy = "cars")
	private Set<Accident> accidents = new HashSet<Accident>();

	public Car() {
	}

	public Car(String licenseID, String model, Integer year, Person person, Policy policy, Set<Accident> accidents) {
		super();
		this.licenseID = licenseID;
		this.model = model;
		this.year = year;
		this.person = person;
		this.policy = policy;
		this.accidents = new HashSet<Accident>();
	}

	public void addAccident(Accident accident) {
		this.accidents.add(accident);
		accident.getCars().add(this);
	}

	public void removeAccident(Accident accident) {
		this.accidents.remove(accident);
		accident.getCars().remove(this);
	}

	public String getLicenseID() {
		return licenseID;
	}

	public void setLicenseID(String licenseID) {
		this.licenseID = licenseID;
	}

	public String getModel() {
		return model;
	}

	public void setModel(String model) {
		this.model = model;
	}

	public Integer getYear() {
		return year;
	}

	public void setYear(Integer year) {
		this.year = year;
	}

	public Person getPerson() {
		return person;
	}

	public void setPerson(Person person) {
		this.person = person;
	}

	public Policy getPolicy() {
		return policy;
	}

	public void setPolicy(Policy policy) {
		this.policy = policy;
	}

	public Set<Accident> getAccidents() {
        if (accidents == null) {
            accidents = new HashSet<>(); 
        }
        return accidents;
    }

    public void setAccidents(Set<Accident> accidents) {
        this.accidents = accidents != null ? accidents : new HashSet<>();
    }
	
	

	public String toString() {
	    return "Car[licenseID=" + licenseID + ", model=" + model + ", year=" + year + "]";
	}

	@Override
	public int hashCode() {
		return Objects.hash(licenseID, model, year);
	}

	@Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Car other = (Car) obj;
        return Objects.equals(licenseID, other.licenseID); 
    }

}
