package com.defamation.backend.service;

import com.defamation.backend.domain.Model;
import com.defamation.backend.repository.ModelRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class DefamationModelService {

    private final ModelRepository modelRepository;

    /**
     * enabled = true 인 모델 목록 조회
     */
    public List<Model> getEnabledModels() {
        return modelRepository.findByEnabledTrueOrderByIdAsc();
    }
}
