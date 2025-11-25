package com.defamation.backend.domain;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "models")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Model {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 내부 식별자 (HF id나 네가 넣은 name)
    @Column(nullable = false, unique = true, length = 100)
    private String name;

    // UI 표시용
    @JsonProperty("display_name") // 프론트가 display_name으로 받게
    @Column(name = "display_name", length = 100)
    private String displayName;

    // enabled = 1/0
    @Column(nullable = false)
    private Boolean enabled = true;
}
