package com.defamation.backend.repository;

import com.defamation.backend.domain.Model;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ModelRepository extends JpaRepository<Model, Long> {

    List<Model> findByEnabledTrueOrderByIdAsc();

    Optional<Model> findByName(String name);
}
