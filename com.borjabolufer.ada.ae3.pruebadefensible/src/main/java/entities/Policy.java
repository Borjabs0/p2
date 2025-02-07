package entities;

import java.util.Objects;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "POLICY_BB04")
public class Policy {
	@Id
	@Column(name = "POLICY_ID", nullable = true)
	private String policyId;

	@OneToOne
	@JoinColumn(name = "LICENSE_ID", unique = true, nullable = false)
	private Car car;

	public Policy() {
	}

	public Policy(String policyId, Car car) {
		super();
		this.policyId = policyId;
		this.car = car;
	}

	public String getPolicyId() {
		return policyId;
	}

	public void setPolicyId(String policyId) {
        this.policyId = (policyId != null && policyId.trim().isEmpty()) ? null : policyId;
    }

	public Car getCar() {
		return car;
	}

	public void setCar(Car car) {
		this.car = car;
	}

	@Override
	public String toString() {
		return "Policy [policyID=" + policyId + ", car=" + car + "]";
	}

	@Override
	public int hashCode() {
		return Objects.hash(policyId);
	}

	@Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Policy other = (Policy) obj;
        return Objects.equals(policyId, other.policyId); 
    }

}
